# self-hosted-ad-password-reset-app

Solution Architect:

![pass-reset-web-app](https://github.com/ashaf3/self-hosted-ad-password-reset-app/assets/30082580/9e4ae087-729f-48b6-a741-9639406dc0ff)

Will upload the code for index.html and Lambda call(python script), powershell script(to update the token)

Lambda is working on two phase: 
  - First its check the token validation, if it matches
  - It does the API call for DS service and updates the user-password.
    {
   "DirectoryId": "string",
   "NewPassword": "string",
   "UserName": "string"
}

