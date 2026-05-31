import grpc
import logging
from concurrent import futures
from . import auth_pb2 as auth_pb2
from . import auth_pb2_grpc as auth_pb2_grpc
from sqlalchemy import select
from app.database import SyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

class UserServiceServicer(auth_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        logger.info("gRPC GetUser called for email: %s", request.email)
        with SyncSessionLocal() as db:
            if not request.email:
                return auth_pb2.UserResponse(found=False)
            
            user = db.execute(select(User).where(User.email == request.email)).scalar_one_or_none()
            if user is None:
                return auth_pb2.UserResponse(found=False)

            return auth_pb2.UserResponse(id=user.id, email=user.email, is_active=user.is_active, found=True)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    logger.info("gRPC server is running on port 50051...")
    server.start()
    server.wait_for_termination()