
### 🗃 Extract Text from Images & PDFs using AWS Textract Service

<div align="center">
  <img src="/assets/UI.png" width="70%"/>
</div>
</br>


## To Run (Locally)

1. Git clone the project repository on your local system
```
git clone https://github.com/deepeshdm/Textract-Web-App.git
```

2. Install dependencies in requirements.txt
```
pip install -r requirements.txt
```

3. In your AWS account create an IAM user and attach required policies to give this user full access of AWS S3 & Textract service.

4. Generate the access keys for this IAM user through your AWS account and put them in an .env file inside the repo.
```
AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=ap-south-1
```

5. Start the streamlit server on localhost.
```
streamlit app.py
```







