import grpc
import logging
from . import auth_pb2 as user_pb2
from . import auth_pb2_grpc as user_pb2_grpc

logger = logging.getLogger(__name__)

def get_user_by_email(email: str):
    channel = grpc.insecure_channel('auth-service:50051')
    stub = user_pb2_grpc.UserServiceStub(channel)

    try:
        request = user_pb2.GetUserRequest(email=email)
        response = stub.GetUser(request)

        if response.found:
            return response
        return None
    except grpc.RpcError as e:
        print(f"gRPC error: {e.code()} - {e.details()}")
        return None
    finally:
        channel.close()