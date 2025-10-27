FROM codercom/code-server:latest

USER root

# Install Python 3 + venv
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Create virtualenv in /opt/venv
RUN python3 -m venv /opt/venv

# Ensure venv is used by default for all users, including in code-server terminals
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies into the venv
RUN pip install --no-cache-dir pandas

# Optional: add a default shell profile to activate venv automatically
RUN echo "export PATH=/opt/venv/bin:\$PATH" >> /etc/profile.d/venv.sh

USER coder
WORKDIR /home/coder/project
