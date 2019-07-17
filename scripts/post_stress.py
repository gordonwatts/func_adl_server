# Run the same query a lot.
import sys
from write_ast import generate_ast
import os
import pickle
import requests
import json
import time
import asyncio
import aiohttp

async def send_ast_msg (data, base_url:str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{base_url}/query', headers={"content-type": "application/octet-stream"},  data=data) as resp:
                dr = json.loads(await resp.text())
                print(f'  {resp.status}: {dr}')
    except BaseException as e:
        print (f'  --> exception {str(e)}')

async def run_it_async(ast, address:str, interval:int=1, count:int=1, how_many:int=100):
    # Next, run what is needed.
    for i in range(0, count):
        print (f"{i}: Firing off {how_many} requests")
        all_of_them = [send_ast_msg(ast, address) for _ in range(0, how_many)]
        await asyncio.gather(*all_of_them)

def run_it(ast_number:int, address:str, interval:int=2, count:int=10):
    # Get the AST:
    a = generate_ast(ast_number)
    d = pickle.dumps(a)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_it_async(d, address, interval, count))

if __name__ == "__main__":
    bad_args = len(sys.argv) != 3
    bad_args = bad_args or not str.isdigit(sys.argv[1])

    if bad_args:
        print ('Usage: python post_ast.py <ast-number> <url>')
        print ('  url is in the form http://localhost:8000, for example.')
    else:
        run_it(int(sys.argv[1]), sys.argv[2])
