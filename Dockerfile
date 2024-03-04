RUN python -m venv --copies /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install SomePackage==1.0.0
RUN pip install AnotherPackage==2.0.0
# Repite el comando RUN pip install para cada dependencia, una por una
