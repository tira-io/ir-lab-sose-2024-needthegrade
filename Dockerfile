# A prepared image with python3.10, java 11, ir_datasets, tira, and PyTerrier installed 
FROM webis/ir-lab-wise-2023:0.0.4

# Update the tira command to use the latest version
RUN pip3 uninstall -y tira \
	&& pip3 install tira \
	&& pip install openai \
    && pip install nltk \
	&& pip install pandas

RUN mkdir -p /usr/nltk_data && \
    python3 -c "import nltk; nltk.download('stopwords', download_dir='/usr/nltk_data')"
ENV JAVA_OPTS="-Xmx4g"
ADD . /app

