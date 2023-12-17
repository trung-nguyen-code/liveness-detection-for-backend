from enum import Enum

class RPC_Mapping(Enum):
    """RPC_Mapping is a mapping between model name and its input name in gRPC request"""

    sunglasses = "input_2"
    face_mask = "input_3"
    nude_nonude = "input_4"