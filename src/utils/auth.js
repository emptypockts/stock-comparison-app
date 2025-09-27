import axios from "axios";
export const verifyToken = async () => {

  const token = localStorage.getItem('token');
  if (!token) {
    console.error('not a valid token')
    return false;
  }
  try {
    const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/verify`, null, {
      headers: {
        'token': token,
      },
    });

    return response.data.success;

  } catch (error) {
    console.error('Error verifying token ', error)
    return false;
  }
};

export const verifyCfToken = async () => {
  const flag = import.meta.env.VITE_DEV_FLAG
  
  if (flag==1){
    return true
  }
  try {
    const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/cfToken`)
    localStorage.setItem('user_id',response.data.upn)
    return response.data.success;
  }
  catch (err) {
    console.error('error verifying cf token', err)
    return false;
  }

}


