FROM pgvector/pgvector:pg15

# Build zhparser (Chinese full-text search parser for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    wget \
    postgresql-server-dev-15 \
    && rm -rf /var/lib/apt/lists/*

# Build SCWS (Simple Chinese Word Segmentation) — zhparser depends on it
RUN wget -q http://www.xunsearch.com/scws/down/scws-1.2.3.tar.bz2 \
    && tar xf scws-1.2.3.tar.bz2 \
    && cd scws-1.2.3 \
    && ./configure --prefix=/usr/local \
    && make -j$(nproc) \
    && make install \
    && cd .. && rm -rf scws-1.2.3 scws-1.2.3.tar.bz2

# Build and install zhparser
RUN git clone --depth 1 https://github.com/amutu/zhparser.git \
    && cd zhparser \
    && make -j$(nproc) \
    && make install \
    && cd .. && rm -rf zhparser

# Clean up build dependencies (keep runtime libs)
RUN apt-get remove -y build-essential postgresql-server-dev-15 git wget \
    && apt-get autoremove -y \
    && apt-get clean
