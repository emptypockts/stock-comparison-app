import axios from "axios";
export const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) return false;
      try {
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/verify`, null, {
          headers: {
            'token': token,
          },
        });
        console.log('valid token',response.data.success)
        return response.data.success;
        
      } catch (error) {
        console.error('Error verifying token ', error)
        return false;
      }
    };

  