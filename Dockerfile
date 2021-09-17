FROM public.ecr.aws/lambda/python:3.8

COPY app.py requirements.txt .env ./
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["app.lambda_handler"]