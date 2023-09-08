import modal
import os

stub = modal.Stub("stable-diffusion-webui")
volume = modal.NetworkFileSystem.new().persisted("stable-diffusion-webui")

@stub.function(
    modal.Image.from_registry("nvidia/cuda:12.2.0-base-ubuntu22.04", add_python="3.11")
    .run_commands(
        "apt update -y && \
        apt install -y software-properties-common && \
        apt update -y && \
        add-apt-repository -y ppa:git-core/ppa && \
        apt update -y && \
        apt install -y git git-lfs && \
        git --version  && \
        apt install -y aria2 libgl1 libglib2.0-0 wget && \
        pip install -q torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 torchtext==0.15.2 torchdata==0.6.1 --extra-index-url https://download.pytorch.org/whl/cu118 && \
        pip install -q xformers==0.0.20 triton==2.0.0 packaging==23.1"
    ),
    network_file_systems={"/content/stable-diffusion-webui": volume},
    gpu="T4",
    timeout=60000,
)
@modal.wsgi_app()
def flask_app():
    os.system(f"git clone -b v2.6 https://github.com/camenduru/stable-diffusion-webui /content/stable-diffusion-webui")
    os.chdir(f"/content/stable-diffusion-webui")
    # os.system(f"rm -rf /content/stable-diffusion-webui/repositories")
    os.system(f"git reset --hard")
    os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/counterfeit-xl/resolve/main/counterfeitxl_v10.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o counterfeitxl_v10.safetensors")
    os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/juggernaut-xl/resolve/main/juggernautXL_version2.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o juggernautXL_version2.safetensors")
    os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/sd_xl_refiner_1.0/resolve/main/sd_xl_refiner_1.0_0.9vae.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o sd_xl_refiner_1.0_0.9vae.safetensors")
    os.environ['HF_HOME'] = '/content/stable-diffusion-webui/cache/huggingface'
    
    from flask import Flask, jsonify
    web_app = Flask(__name__)
    @web_app.route('/start')
    def start():
        command = f"python launch.py --cors-allow-origins=* --xformers --theme dark --gradio-queue --share"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print("Command executed successfully.")
            print("Standard Output:")
            print(result.stdout)
            return jsonify({"message": result.stdout})
        else:
            print("Command failed.")
            print("Standard Output:")
            print(result.stdout)
            print("Standard Error:")
            print(result.stderr)
            return jsonify({"error": "error"})
    return web_app

# async def run():
#     os.system(f"git clone -b v2.6 https://github.com/camenduru/stable-diffusion-webui /content/stable-diffusion-webui")
#     os.chdir(f"/content/stable-diffusion-webui")
#     # os.system(f"rm -rf /content/stable-diffusion-webui/repositories")
#     os.system(f"git reset --hard")
#     os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/counterfeit-xl/resolve/main/counterfeitxl_v10.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o counterfeitxl_v10.safetensors")
#     os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/juggernaut-xl/resolve/main/juggernautXL_version2.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o juggernautXL_version2.safetensors")
#     os.system(f"aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/ckpt/sd_xl_refiner_1.0/resolve/main/sd_xl_refiner_1.0_0.9vae.safetensors -d /content/stable-diffusion-webui/models/Stable-diffusion -o sd_xl_refiner_1.0_0.9vae.safetensors")
#     os.environ['HF_HOME'] = '/content/stable-diffusion-webui/cache/huggingface'
#     os.system(f"python launch.py --cors-allow-origins=* --xformers --theme dark --gradio-queue --share")

# @stub.local_entrypoint()
# def main():
#     run.call()
