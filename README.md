# DevOps Experts - Final Project #

---

## Description ##
• DevOps Experts Course - Final Project.

• Python Backend & Frontend.

• The Project Includes 4 Parts - [MySQL & Python , Jenkins , Docker , K8S & HELM].

---

## Topics ##
> Python

> Selenium

> REST API

> MySQL

> Web Interface

> Flask

> Docker

> Docker Compose

> K8S

> HELM

---

## Libraries ##
- pymysql

- requests

- flask

- selenium

- webdriver

- prettytable

- socket

---

## Installations ##
```bash
pip install --ignore-installed pymysql requests selenium flask prettytable
```

---

## API Reference ##
```bash  
Require running `rest_app.py` (Currently it points to : "http://127.0.0.1:5000/${user_id}").
```

---

## REST Application ##

### Create New User ###
```bash  
POST `/users/${user_id}`
```
| Parameter | Type  | 
|:----------|:------|
| `user_id` | `int` |

#### Request Body (Json) ####
```json  
{
    "status"    : "OK",
    "user_added": "${user_name}"
}
```

### Update User Name ###
```bash  
PUT `/users/${user_id}`
```
| Parameter | Type  | 
|:----------|:------|
| `user_id` | `int` | 

#### Request Body (Json) ####
```json  
{
    "status"      : "OK",
    "user_updated": "${user_name}"
}
```

### Get User ###
```bash
GET `/users/${user_id}`
```
| Parameter | Type  |
|:----------|:------|
| `user_id` | `int` |

#### Request Body (Json) ####
```json  
{
    "status"   : "OK",
    "user_name": "${user_name}"
} 
```

### Get All Users ###
```bash
GET `/users/get_all_users`
```
| Parameter |  Type  |
|:----------|:-------|
|   `None`  | `None` |

#### Request Body (Json) ####
```json  
[
    {
        "creation_date": "${creation_date}",
        "user_id"      : "${user_id}",
        "user_name"    : "${user_name}"
    },
    {
        "creation_date": "${creation_date}",
        "user_id"      : "${user_id}",
        "user_name"    : "${user_name}"
    }
] 
```

### Delete User ###
```bash
DELETE `/users/${user_id}`
```
| Parameter | Type  |
|:----------|:------|
| `user_id` | `int` |

#### Request Body (Json) ####
```json  
{
    "status"      : "OK",
    "user_deleted": "${user_id}"
} 
```

---

## Web Application ##
```bash
[URL]    "http://127.0.0.1:5001/${user_id}".
[Return] Return HTML page with `${user_name}` from DB.
```

### Get User Data ###
```bash
GET `/users/get_user_data/${user_id}`
```
| Parameter | Type  |
|:----------|:------|
| `user_id` | `int` |

```bash
[Good Case] Response : 
return "<h1 id='user'>" + "`user name` is : " + user_name + "</h1>"

[Bad Case] Response :
return "<h1 id='error'>" + "No such `user id` : " + str(user_id) + "</h1>"
```

---

## Testing ##
```bash
Tests Are : [backend_testing.py, frontend_testing.py, combined_testing.py].
```

```bash
In order to perform testings, please run `rest_app.py` & `web_app.py`.
```

---

## Chrome Driver ##
```bash
Chrome Web Driver supporting Chrome Version 108.0.5359.125 (Official Build) (64-bit).
```

---

## Jenkins - Algorithm ##
```bash
1 - Clone GIT Repository.
2 - Install Packages.
3 - Start Flask Server (REST API).
4 - Start Flask Server (WEB APP).
5 - Drop DB Tables (If Exists Already).
6 - Run Test (Backebd).
7 - Run Test (Frontend).
8 - Run Test (Combined).
9 - Stop Flask Servers (REST API, WEB APP).
```

---

## Docker ##
### Docker Compose Instructions ###
```bash
1 - Create 'docker-compose.yml' locally on your machine.
2 - Create '.env' locally on your machine.
3 - Run docker compose with the following command : 'docker-compose --env-file .env --file docker-compose.yml up'.
```

---

## K8S ##
```bash
1 - Follow the steps of 'Docker Compose Instructions'.
2 - Use with Minikube command : 'minikube start'.
3 - Create HELM chart locally on your machine with the following command : 'helm install <HELM Chart Name> <HELM Path>'.
```

---

## Authors ##
[@Din-Golan](https://www.github.com/DinGolan)

---
