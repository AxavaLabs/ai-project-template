
import torch
import runpod
from loguru import logger
import time
import asyncio

logger.info(f"torch version: {torch.__version__} need cuda version: {torch.version.cuda}")

from src import pull_file_from_s3, push_image_to_s3
from src import inference


def process_job(job):
    logger.info(f"New process job: {job}")
    
    job_input = job["input"] 
    image_url = job_input.get('image_url', "example.com")

    # Pull
    start = time.time()
    image = pull_file_from_s3(image_url)
    logger.info(f"Download image time: {time.time() - start}s")
    
    # Inference
    start = time.time()
    imgs = inference(image)
    logger.info(f"Inference time: {time.time() - start}s")
    
    # Push
    start = time.time()
    results = []
    for i, img in enumerate(imgs):
        output_name = f'out_{i}.jpg'
        s3_url = push_image_to_s3(img, output_name)
        results.append(s3_url)
    logger.info(f"Push image time: {time.time() - start}s")
    
    logger.info(f"Results: {results}")
    logger.success(f"Process job done")
    
    return results

async def handler(job):
    if "wake_up" in job["input"]:
        return True
    
    results = await asyncio.to_thread(process_job, job)
    return results

if __name__ == '__main__':
    runpod.serverless.start({"handler": handler})
