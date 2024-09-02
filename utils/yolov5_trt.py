import cv2
import numpy as np
# image = np.zeros((512, 512, 3), np.uint8)
# cv2.imshow('image', image)
# cv2.waitKey(1)
# cv2.destroyWindow('image')
import torch
from torchvision.ops import nms
from PIL import Image,ImageOps
import matplotlib.pyplot as plt
import torch
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
def resize_img( im):
    target_size = 640   # 目标尺寸
    width, height = im.size
    if width < height:
        new_height = target_size
        new_width = int(new_height / height * width)
    else:
        new_width = target_size
        new_height = int(new_width / width * height)
    resized_im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
    pad_width = target_size - new_width
    pad_height = target_size - new_height
    
    # 计算每边需要补的像素数
    left_pad = pad_width // 2
    right_pad = pad_width - left_pad
    top_pad = pad_height // 2
    bottom_pad = pad_height - top_pad
    # print(top_pad,top_pad)
    # 补hui色边
    new_im = ImageOps.expand(resized_im, border=(left_pad, top_pad, right_pad, bottom_pad), fill=(114, 114, 114))
    
    return new_im,top_pad
def from_numpy( x):
    """Converts a NumPy array to a torch tensor, maintaining device compatibility."""
    return torch.from_numpy(x) if isinstance(x, np.ndarray) else x

def box_iou(box1, box2, eps=1e-7):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.

    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    (a1, a2), (b1, b2) = box1.unsqueeze(1).chunk(2, 2), box2.unsqueeze(0).chunk(2, 2)
    inter = (torch.min(a2, b2) - torch.max(a1, b1)).clamp(0).prod(2)

    # IoU = inter / (area1 + area2 - inter)
    return inter / ((a2 - a1).prod(2) + (b2 - b1).prod(2) - inter + eps)
def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y
def xyxy2xywh(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right."""
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 2] = x[..., 2] - x[..., 0] / 2  # bottom right x
    y[..., 3] = x[..., 3] - x[..., 1] / 2  # bottom right y
    return y
def NonMaximumSuppression(
    prediction,
    conf_thres=0.15,
    iou_thres=0.45,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=300,
    nm=0,  # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping detections.

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output

    device = prediction.device
    mps = "mps" in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        mask = x[:, mi:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections
        if merge and (1 < n < 3e3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)

    return output
def non_max_suppression(
    prediction,
    conf_thres=0.4,
    iou_thres=0.35,
    classes=None,
    agnostic=False,
    multi_label=False,
    labels=(),
    max_det=1000,
    nm=0,  # number of masks
):
    """
    Non-Maximum Suppression (NMS) on inference results to reject overlapping detections.

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    # Checks
    assert 0 <= conf_thres <= 1, f"Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0"
    assert 0 <= iou_thres <= 1, f"Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0"
    if isinstance(prediction, (list, tuple)):  # YOLOv5 model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output
    device = prediction.device
    mps = "mps" in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[2] - nm - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates
    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 0.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    mi = 5 + nc  # mask start index
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence
        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        # x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box/Mask
        box = xywh2xyxy(x[:, :4])  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        # box = x[:, :4]  # center_x, center_y, width, height) to (x1, y1, x2, y2)

        mask = x[:, 6:]  # zero columns if no masks

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:mi] > 0).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 5 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = x[:, 5:mi].max(1, keepdim=True)
            x = torch.cat((box, x[..., 4:5], j.float(), mask), 1)[conf.view(-1) > 0]
        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        # print(scores)
        i = nms(boxes, scores, iou_thres)  # NMS
        i = i[:max_det]  # limit detections
        if merge and (1 < n < 3e3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)

    return output
import threading
import time
class YOLOv5:
    def __init__(self, model_path,image_queue,infer_queue,show_queue):
        # TensorRT日志记录器
        # self.label = ['Hero', 'arrow', 'gate', 'hero', 'item', 'monster', 'monster_faker', 'white_arrow']
        self.label = ['Monster', 'Monster_ds', 'Monster_szt', 'card', 'equipment', 'go', 'hero', 'map', 'opendoor_d', 'opendoor_l', 'opendoor_r', 'opendoor_u', 'pet', 'Diamond']
        # self.TRT_LOGGER = trt.Logger(trt.Logger.ERROR)
        # self.engine = self.load_engine(model_path)
        # self.host_mem,self.cuda_mem, self.bindings, self.stream = self.allocate_buffers(self.engine)
        # self.context = self.engine.create_execution_context()
        self.path = model_path
        self.image_queue = image_queue
        self.infer_queue = infer_queue
        self.show_queue = show_queue
        self.thread = threading.Thread(target=self.thread)  # 创建线程，并指定目标函数
        self.thread.daemon = True  # 设置为守护线程（可选）
        self.thread.start()
    def thread(self):
        context = cuda.Device(0).make_context()
        self.TRT_LOGGER = trt.Logger(trt.Logger.ERROR)
        self.engine = self.load_engine(self.path)
        self.host_mem,self.cuda_mem, self.bindings, self.stream = self.allocate_buffers(self.engine)
        self.context = self.engine.create_execution_context()
        while True:
            if self.image_queue.empty():
                time.sleep(0.005)
                continue
            image = self.image_queue.get()
            output = self.process(image)
            self.infer_queue.put([image,output])
            self.show_queue.put([image,output])
        context.pop()
    def from_numpy(self,x):
        """Converts a NumPy array to a torch tensor, maintaining device compatibility."""
        return torch.from_numpy(x) if isinstance(x, np.ndarray) else x
    def process(self,img):
        # start_time = time.time()
        image = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        image,top_pad = resize_img(image)
        image_array = np.array(image).transpose((2, 0, 1))
        image_array = np.expand_dims(image_array, axis=0).astype(np.float32).ravel()
        inputs = image_array / 255.0
        np.copyto(self.host_mem[0], inputs)
        output_data = self.do_inference(self.context, self.host_mem, self.cuda_mem, self.bindings, self.stream)
        shape = (1,25200,19)
        output = np.resize(output_data[1], shape)
        output = self.from_numpy(output)
        output = NonMaximumSuppression(output)[0]
        output[:,0] = output[:,0]/640
        output[:,1] = (output[:,1] - top_pad)/(640-top_pad*2)
        output[:,2] = output[:,2]/640
        output[:,3] = (output[:,3] - top_pad)/(640-top_pad*2)
        # end_time = time.time()
        # print(f'time taken: {end_time - start_time:.4f} seconds')
        return output 
    # 从磁盘加载序列化好的TensorRT引擎
    def load_engine(self,engine_file_path):
        # Load the TensorRT engine
        with open(engine_file_path, "rb") as f, trt.Runtime(self.TRT_LOGGER) as runtime:
            engine = runtime.deserialize_cuda_engine(f.read())
            if engine is None:
                raise ValueError(f"Failed to load engine from {engine_file_path}")
            return engine
    # 为输入输出数据分配缓冲区
    def allocate_buffers(self,engine):
        bindings = []
        host_mem = []
        cuda_mem = []
        stream = cuda.Stream()
        # 获取输入和输出tensor的数量
        num_bindings = engine.num_bindings
        for binding in range(num_bindings):
            size = trt.volume(engine.get_binding_shape(binding))
            dtype = trt.nptype(engine.get_binding_dtype(binding))
            # 根据是输入还是输出，分配主机和设备缓冲区
            if engine.binding_is_input(binding):
                # 输入缓冲区
                host_buf = cuda.pagelocked_empty(size, dtype)
                cuda_buf = cuda.mem_alloc(host_buf.nbytes)
            else:
                # 输出缓冲区
                host_buf = cuda.pagelocked_empty(size, dtype)
                cuda_buf = cuda.mem_alloc(host_buf.nbytes)
            # 添加到列表中
            bindings.append(int(cuda_buf))
            host_mem.append(host_buf)  # 保存主机内存指针，以便后续使用
            cuda_mem.append(cuda_buf)
        return host_mem, cuda_mem, bindings, stream
    def do_inference(self,context, host_mem, cuda_mem, bindings, stream, batch_size=1):
        # 输入数据的传输
        [cuda.memcpy_htod_async(inp_device, inp_host, stream) for inp_host, inp_device in zip(host_mem, cuda_mem)]
        # 执行模型
        context.execute_async(bindings=bindings,stream_handle=stream.handle)
        # 输出数据传回主机
        [cuda.memcpy_dtoh_async(out_host, out_device, stream) for out_host, out_device in zip(host_mem, cuda_mem)]
        # 等待数据传输结束
        stream.synchronize()
        # 输出数据
        return [out_host for out_host in host_mem]
    
if __name__ == '__main__':
    yolo = YOLOv5("/home/linux/workspace/dnfm/dnfm-yolo-tutorial/utils/dnfm.trt")
    image = cv2.imread("/home/linux/workspace/dnfm/dnfm-yolo-tutorial/utils/1723298258954.jpg")
    output = yolo.process(image)
    for boxs in output:
            # 把坐标从 float 类型转换为 int 类型
            det_x1, det_y1, det_x2, det_y2,conf,label = boxs
            # 裁剪目标框对应的图像
            x1 = int(det_x1*image.shape[1])
            y1 = int(det_y1*image.shape[0])
            x2 = int(det_x2*image.shape[1])
            y2 = int(det_y2*image.shape[0])
            # 绘制矩形边界框
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, "{:.2f}".format(conf), (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            cv2.putText(image, yolo.label[int(label)], (int(x1), int(y1-30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    cv2.imshow("test", image)
    cv2.waitKey(0)
    print(output)
    exit()