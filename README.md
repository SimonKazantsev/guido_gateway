guido_gateway

api gateway, перенаправляет запросы в микросервисы, единственная точка входа для клиента, часть диплома.



Запросы для проверки системы


*/auth/register
```json
{
  "username": "user1",
  "email": "user@example.com",
  "password": "PasswordUser1!"
}
```

*/auth/login
```json
{
  "fingerprint": "string",
  "identifier": "user1",
  "password": "PasswordUser1!"
}
```
