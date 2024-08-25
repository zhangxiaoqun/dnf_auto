
'''
onnx 1.16.2
TensorRT-8.5.3.1.Windows10.x86_64.cuda-11.8.cudnn8.6
CUDA 11.8

'''

import onnx
import numpy


# 加载 ONNX 模型
model = onnx.load('./dnf_sm.onnx')
# 遍历模型的所有权重
for initializer in model.graph.initializer:
    if initializer.data_type == onnx.TensorProto.INT64:
        # 将 INT64 权重转换为 INT32
        int64_data = onnx.numpy_helper.to_array(initializer)
        int32_data = int64_data.astype(numpy.int32)
        initializer.CopyFrom(onnx.numpy_helper.from_array(int32_data, initializer.name))
        initializer.data_type = onnx.TensorProto.INT32

# 保存修改后的模型
# onnx.save(model, 'dnf_sm32.onnx')


