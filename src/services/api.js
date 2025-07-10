import axios from "axios"

export default axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 5000,
  withCredentials: true, // Enables cookies to be sent, including the sessionid
  xsrfCookieName: "csrftoken", // CSRF cookie name
  xsrfHeaderName: "X-CSRFTOKEN", // CSRF header name
  withXSRFToken: true // Ensures that the CSRF token is included
})
