ARG BUILD_FROM
FROM $BUILD_FROM

ARG BUILD_ARCH
RUN apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    python3 \
    py3-pip \
    jpeg-dev \
    zlib-dev

WORKDIR /app

COPY app/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ .
COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
