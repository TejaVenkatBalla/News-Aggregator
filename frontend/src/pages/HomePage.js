import React from 'react';
import { useAuth } from '../AuthContext';
import NewsList from '../components/NewsList';

const HomePage = () => {
  const { user, logout } = useAuth();

  return (
    <div className="home-page">
      <header>
        <h1>Latest Event News</h1>
        {user && (
          <div className="user-info">
            <p>Welcome, {user.email}!</p>
            <button onClick={logout}>Logout</button>
          </div>
        )}
      </header>
      <main>
        <NewsList />
      </main>
    </div>
  );
};

export default HomePage;
