# How to get free subdomain?

1) Fork the Code

2) Add the following content under the subdomain you want:
```json
    "example.com" {
        //...other subdomains
    
        "subdomain that you want": {
            "content":"target site",
            "type":"A/CNAME",
            "github_username":"your username"
        }

    }
//note, if you are targetting a github.io page then use CNAME
```

3) Perform a PR, an admin will help you setup your domain