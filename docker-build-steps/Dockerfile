FROM tensorflow/tensorflow:1.14.0-gpu
RUN mkdir -p /snel \
        && mkdir -p /bucket
RUN apt-get update \
    && apt-get install -y \
        nmap \
	vim \
	tmux \
	nano \
	moreutils \
        git
ADD . /snel
RUN pip install pymongo future grpcio==1.30.0 protobuf==3.12.2 tensorflow-probability==0.7.0
ENV PATH "/snel/lfadslite/:${PATH}"
ENV PYTHONPATH "/snel/autoLFADS-beta/pbt_opt/:${PYTHONPATH}"
ENV PYTHONPATH "/snel/lfadslite/:${PYTHONPATH}"
EXPOSE 80
