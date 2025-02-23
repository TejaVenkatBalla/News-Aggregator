import React, { useState } from 'react';

import './RegisterPage.css';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const RegisterPage = () => {
  const navigate = useNavigate();

  const [message, setMessage] = useState(''); // State for message
  const handleSubmit = async (e) => {

    e.preventDefault();
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password
        }),
      });

      const data = await response.json(); // Parse the response

      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }

      setMessage('Registration successful! You can now log in.'); // Success message

      navigate('/login');
    } catch (error) {
      setMessage(error.message); // Display error message

    }
  };

  return (
    <div className="register-page"> 
      <h2>Register</h2>
      {message && <p>{message}</p>} 

      <form onSubmit={handleSubmit}>
        <input name="email" type="email" placeholder="Email" required />
        <input name="password" type="password" placeholder="Password" required />
        <button type="submit">Register</button>
      </form>
      <p>
        Already have an account? <a href="/login">Login here</a>
      </p>
    </div>
  );
};

export default RegisterPage;
