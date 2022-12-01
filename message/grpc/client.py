import asyncio
import logging

import grpc
import icarus_pb2
import icarus_pb2_grpc


async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = icarus_pb2_grpc.GreeterStub(channel)
        response = await stub.SayHello(icarus_pb2.HelloRequest(name="you"))
    print("Client Received: " + response.message)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(run())