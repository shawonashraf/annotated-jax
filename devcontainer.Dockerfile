FROM python:3.12.8-bookworm

# creates directories for hf cache and wandb keys
WORKDIR /workspaces
RUN mkdir -p /workspaces/.cache/huggingface
RUN chmod -R 777 /workspaces/.cache/huggingface
ENV HF_HOME=/workspaces/.cache/huggingface

# env
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv pip install --system .
