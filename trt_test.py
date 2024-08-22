import tensorrt as trt
import onnx

# TensorRT 日志
class TRTLogger(trt.Logger):
    def __init__(self):
        super(TRTLogger, self).__init__()

# 创建一个 TensorRT 构建器
def build_engine(onnx_model_path):
    logger = TRTLogger()
    builder = trt.Builder(logger)
    network = builder.create_network(flags=0)
    parser = trt.OnnxParser(network, logger)

    # 读取ONNX模型并解析
    with open(onnx_model_path, 'rb') as model:
        if not parser.parse(model.read()):
            print('Failed to parse the ONNX model.')
            for err in range(parser.num_errors):
                print(parser.get_error(err))
            return None

    # 配置构建器
    builder.max_batch_size = 1  # 设置最大批处理大小
    builder.max_workspace_size = 1 << 30  # 1GB

    # 构建引擎
    engine = builder.build_cuda_engine(network)
    return engine

# 使用示例
onnx_model_path = './utils/dnfm.onnx'
engine = build_engine(onnx_model_path)

# 保存引擎
with open('./utils/dnfm.trt', 'wb') as f:
    f.write(engine.serialize())


