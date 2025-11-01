import axios from "axios";
import { useAppStore } from "@/stores/app"; 

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASEURL || "http://localhost:8000/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else       resolve(token);
  });
  failedQueue = [];
}



api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response, config } = error;
    const originalRequest = config;

    // se for 401 e ainda não tentou retry
    if (response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        // dispara o login modal
        useAppStore().triggerLoginModal();
      }

      // retorna uma nova Promise que ficará pendente até o usuário logar
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((newToken) => {
          // ajusta o token do header e refaz o request
          originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err))
        .finally(() => {
          isRefreshing = false;
        });
    }

    return Promise.reject(error);
  }
);




const ApiService = {
  login: async (usuario, senha) => {
    const response = await api.post(
      "/users/login",
      {
        username: usuario,
        password: senha,
      },
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );
    return response.data;
  },
  getUserLogged: () => api.get("/users/logged").then(r => r.data),
  getRoutines: ()    => api.get("/routines").then(r => r.data),
  getAssignedRoutines: () => api.get("/routines/conclude").then(r => r.data), //precisa de ajustes para o futuro onde outros utilizarão o sistema.
  completeRoutine: id => api.put(`/routines/${id}/complete`).then(r => r.data),  
  getClients:  ()    => api.get("/clients").then(r => r.data),
  getUsers:    ()    => api.get("/users/").then(r => r.data),
  forgotPassword: e  => api.post(`/users/forgot-password/${e}`).then(r => r.data),
  resetSenha:    (s, t) =>
                      api.post("/users/reset-password", null, { params: { password: s, token: t } })
                         .then(r => r.data),
  signup:       u   => api.post("/users/signup", u).then(r => r.data),
  salvarRotina: r   => api.post("/routines/", {
                        titulo: r.titulo,
                        descricao: r.descricao,
                        dt_vencimento: r.dt_vencimento,
                        hr_estimativa: r.hr_estimativa,
                        clients_id: r.user_client,
                      }).then(r => r.data),
  getAssignedClients: userid => api.get(`/users-clients/assigned/${userid}`).then(r => r.data), 
  deleteRoutine: id => api.delete("/routines", { params: { routine_id: id } })
                         .then(r => r.data),
  playRoutine : id => api.put(`/routines/${id}/play`)
                        .then(r => r.data),
  pauseRoutine : (id,motivo) => api.put(`/routines/pause/`,{id,motivo})
                        .then(r => r.data),
  updateRoutine : (id,payload) => api.put(`/routines/${id}`,payload)
                        .then(r => r.data),
  deleteUser: id => api.delete(`/users/${id}`).then(r => r.data),
  updateUser: (id, payload) => api.put(`/users/${id}`, payload).then(r => r.data),
  deleteClient:(id) => api.delete(`/clients/${id}`).then(r => r.data),
  createClient: (payload) => api.post("/clients", payload).then(r => r.data),
  updateClient: (id, payload) => api.put(`/clients/${id}`, payload).then(r => r.data),

};
export default ApiService;
export { api, processQueue };
 



