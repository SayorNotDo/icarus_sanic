import asyncio
import logging
import grpc
import icarus_pb2
import icarus_pb2_grpc

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


class Greeter(icarus_pb2_grpc.GreeterServicer):

    async def SayHello(
            self, request: icarus_pb2.HelloRequest,
            context: grpc.aio.ServicerContext) -> icarus_pb2.HelloReply:
        logging.info("Received request: %s", request)
        await asyncio.sleep(4)
        logging.info("Sleep complete, responding")
        return icarus_pb2.HelloReply(message="Hello " + request.name)


async def serve() -> None:
    server = grpc.aio.server()
    icarus_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    listen_addr = 'localhost:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server: %s", listen_addr)
    await server.start()

    async def server_graceful_shutdown():
        logging.info("Starting graceful shutdown")
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(serve())
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
