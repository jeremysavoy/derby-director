import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// PrimeVue imports
import PrimeVue from 'primevue/config'
//import Lara from '@primevue/themes/lara'
//import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// UI Components
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import InputNumber from 'primevue/inputnumber'
import Dialog from 'primevue/dialog'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import FileUpload from 'primevue/fileupload'
import Timeline from 'primevue/timeline'
import Chart from 'primevue/chart'

const app = createApp(App)

// Init Pinia
app.use(createPinia())

// Init Router
app.use(router)

// Init PrimeVue
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)

// Register components
app.component('Button', Button)
app.component('Card', Card)
app.component('InputText', InputText)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Tag', Tag)
app.component('Chip', Chip)
app.component('Dropdown', Dropdown)
app.component('MultiSelect', MultiSelect)
app.component('InputNumber', InputNumber)
app.component('Dialog', Dialog)
app.component('ProgressBar', ProgressBar)
app.component('ProgressSpinner', ProgressSpinner)
app.component('TabView', TabView)
app.component('TabPanel', TabPanel)
app.component('Textarea', Textarea)
app.component('Checkbox', Checkbox)
app.component('FileUpload', FileUpload)
app.component('Timeline', Timeline)
app.component('Chart', Chart)

app.mount('#app')