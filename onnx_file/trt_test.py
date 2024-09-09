#
# import onnx
# import numpy as np
#
# # 加载 ONNX 模型
# model_path = './utils/best.onnx'  # 替换为您的模型路径
# model = onnx.load(model_path)
#
# # 遍历模型的所有初始化参数
# for tensor in model.graph.initializer:
#     if tensor.data_type == onnx.TensorProto.INT64:
#         # 打印当前权重信息
#         print(f"Converting tensor '{tensor.name}' from INT64 to INT32.")
#
#         # 获取当前权重的数据
#         int64_array = np.frombuffer(tensor.raw_data, dtype=np.int64)
#
#         # 转换为 INT32
#         int32_array = int64_array.astype(np.int32)
#
#         # 更新 tensor 的数据类型和权重数据
#         tensor.data_type = onnx.TensorProto.INT32
#         tensor.raw_data = int32_array.tobytes()
#
# # 保存修改后的模型
# onnx.save(model, './utils/converted_model.onnx')
# print("Model has been converted and saved as 'converted_model.onnx'.")
#
#
# import tensorrt as trt
#
# # 创建 TensorRT Logger
# logger = trt.Logger(trt.Logger.WARNING)
#
# # 创建一个 Builder，并设置为显式批处理维度
# builder = trt.Builder(logger)
# network = builder.create_network(flags=1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
#
# # 继续加载 ONNX 模型
# parser = trt.OnnxParser(network, logger)
#
# # 解析 ONNX 模型
# with open("./utils/converted_model.onnx", "rb") as model:
#     if not parser.parse(model.read()):
#         print("ERROR: Failed to parse the model.")
#         for error in range(parser.num_errors):
#             print(parser.get_error(error))
# import tensorrt as trt
# import onnx
#
# print('TensorRT version:', trt.__version__)
# print('ONNX version:', onnx.__version__)

import tensorrt as trt

def build_engine(onnx_file_path, engine_file_path='model.engine'):
    # 创建 TensorRT logger
    logger = trt.Logger(trt.Logger.WARNING)

    # 创建 Builder
    builder = trt.Builder(logger)

    # 创建网络时使用 EXPLICIT_BATCH 标志
    network = builder.create_network(flags=trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)

    # 创建 ONNX Parser
    parser = trt.OnnxParser(network, logger)

    # 读取 ONNX 模型
    with open(onnx_file_path, 'rb') as model_file:
        if not parser.parse(model_file.read()):
            print('ERROR: Failed to parse the ONNX model.')
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return None

    # 创建 Builder Config
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1GB

    # 设置其他必要的构建标志（根据需要）
    config.set_flag(trt.BuilderFlag.ESTIMATE_INITIAL_BOUNDS)

    # 创建 TensorRT 引擎
    engine = builder.build_engine(network, config)

    # 序列化引擎并保存到文件
    with open(engine_file_path, 'wb') as f:
        f.write(engine.serialize())

    print(f"Engine has been saved to {engine_file_path}.")
    return engine

# 使用函数进行转换
onnx_file = "./"  # 替换为您的 ONNX 模型文件路径
build_engine(onnx_file)