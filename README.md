# How to get free subdomain?

1) Make a Pull Request

2) Add the following content under the subdomain you want:
```json
        "subdomain that you want": {
            "content":"target site",
            "type":"A/CNAME",
            "github_username":"your username"
        }
//note, if you are targetting a github.io page then use CNAME
```