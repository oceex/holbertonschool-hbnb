# Testing and Validation Report

## 1. Objective
The goal of this task was to implement validation logic for all entity models (User, Place, Review, Amenity) and ensure the API handles invalid data correctly by returning appropriate error status codes (400 Bad Request).

## 2. Validation Implementation
All entity models now include validation logic within their property setters, raising ValueError when input data violates business rules.

## 3. Test Cases Summary
| Endpoint | Scenario | Expected Status |
| :--- | :--- | :--- |
| POST /users/ | Valid User Creation | 201 Created |
| POST /users/ | Invalid Email | 400 Bad Request |
| POST /places/ | Negative Price | 400 Bad Request |
| POST /places/ | Invalid Latitude | 400 Bad Request |
| POST /reviews/ | Invalid Rating | 400 Bad Request |
| POST /amenities/ | Empty Name | 400 Bad Request |

## 4. Testing Tools Used
* **cURL:** Used for black-box testing of API endpoints.
* **Swagger UI:** Verified endpoint documentation at http://127.0.0.1:5000/api/v1/.
* **unittest:** Implemented automated test cases.

## 5. Conclusion
The implementation successfully validates all required attributes and ensures robustness across the HBnB application.
