import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"

// Documentation of mosha-vue-toastify : https://github.com/szboynono/mosha-vue-toastify
import "mosha-vue-toastify/dist/style.css"

// Documentation of v-calendar : https://vcalendar.io/getting-started/installation.html
import { setupCalendar } from 'v-calendar';
import "v-calendar/style.css"

import "@fortawesome/fontawesome-free/js/all"

const app = createApp(App)
app.use(setupCalendar, {})
app.use(router)
app.mount("#app")
