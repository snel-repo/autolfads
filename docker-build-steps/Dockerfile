FROM tensorflow/tensorflow:1.12.0-gpu
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
RUN pip install pymongo future
ENV PATH "/snel/lfadslite/:${PATH}"
ENV PYTHONPATH "/snel/PBT_HP_opt/pbt_opt/:${PYTHONPATH}"
ENV PYTHONPATH "/snel/lfadslite/:${PYTHONPATH}"
EXPOSE 80