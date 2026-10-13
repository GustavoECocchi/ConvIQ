import './App.css'
import { RouterProvider, createBrowserRouter } from 'react-router'
import { rotas } from './rotas.tsx'

const roteador = createBrowserRouter(rotas)

function App() {
  return <RouterProvider router={roteador} />
}

export default App
