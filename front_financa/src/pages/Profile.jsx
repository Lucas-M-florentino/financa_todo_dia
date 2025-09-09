import React, { useContext, useState } from 'react';
import { ProfileContext } from '../context/ProfileContext';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { profile, isLoading, saveProfile } = useContext(ProfileContext);
  const { logout } = useAuth();

  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState(profile || { name: '', email: '' });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  if (isLoading) return <p>Carregando...</p>;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      await saveProfile(formData); // usa o contexto
      setSuccess('Perfil atualizado com sucesso!');
      setEditing(false);
    } catch (err) {
      console.error('Erro ao atualizar perfil:', err);
      setError('Falha ao atualizar perfil');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Profile</h2>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {success && <p className="text-green-500 mb-4">{success}</p>}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700">Name</label>
          <input
            type="text"
            name="name"
            value={formData.name || ''}
            onChange={handleChange}
            disabled={!editing}
            className={`w-full p-2 border rounded ${!editing ? 'bg-gray-100' : ''}`}
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Email</label>
          <input
            type="email"
            name="email"
            value={formData.email || ''}
            onChange={handleChange}
            disabled={!editing}
            className={`w-full p-2 border rounded ${!editing ? 'bg-gray-100' : ''}`}
          />
        </div>
        {editing ? (
          <div className="flex justify-between">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => {
                setEditing(false);
                setFormData(profile);
                setError(null);
                setSuccess(null);
              }}
              className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Edit Profile
          </button>
        )}
      </form>

      <hr className="my-6" />
      <button
        onClick={logout}
        className="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
};

export default Profile;
