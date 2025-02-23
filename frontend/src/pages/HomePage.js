import React from 'react';
import './HomePage.css';

import { useAuth } from '../AuthContext';
import NewsList from '../components/NewsList';

const HomePage = () => {
  const { logout } = useAuth();


  return (
    <div className="home-page">
      <header>
        <h1>Latest Event News</h1>
        <div className="user-info">
          <button onClick={logout}>Logout</button>
        </div>

      </header>
      <main>
        <NewsList />
      </main>
    </div>
  );
};

export default HomePage;
