# DevOps Experts - Final Project #

---

## Description ##
• DevOps Experts Course - Final Project.

• Python Backend & Frontend Stack.

• The Project Includes 3 Parts.

• Current status : Only the first part has finished. Part 2, 3 will be attach soon ...

---

## Topics ##
> Python

> Selenium

> REST API

> MySQL

> Web Interface

> Flask

---

## Libraries ##
- pymysql

- requests

- flask

- selenium

- webdriver

- prettytable

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

## Authors ##
[@Din-Golan](https://www.github.com/DinGolan)

---
