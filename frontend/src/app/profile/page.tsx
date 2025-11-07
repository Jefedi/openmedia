'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Helper function to get full avatar URL
  const getAvatarUrl = (avatarPath?: string) => {
    if (!avatarPath) return undefined;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:18000';
    const fullUrl = `${apiUrl}${avatarPath}`;
    console.log('Avatar URL constructed:', { avatarPath, apiUrl, fullUrl });
    return fullUrl;
  };

  // Form states
  const [activeTab, setActiveTab] = useState<'profile' | 'email' | 'password' | 'delete'>('profile');

  // Profile update
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [bio, setBio] = useState('');
  const [profileUpdating, setProfileUpdating] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState('');

  // Email update
  const [newEmail, setNewEmail] = useState('');
  const [emailPassword, setEmailPassword] = useState('');
  const [emailUpdating, setEmailUpdating] = useState(false);
  const [emailSuccess, setEmailSuccess] = useState('');
  const [emailError, setEmailError] = useState('');

  // Password update
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordUpdating, setPasswordUpdating] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // Account deletion
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  // Avatar upload
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [avatarError, setAvatarError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch('/api/profile/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        router.push('/login');
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }

      const data = await response.json();
      console.log('Profile data received:', data);
      console.log('Avatar URL from backend:', data.avatar_url);
      setProfile(data);
      setUsername(data.username || '');
      setFullName(data.full_name || '');
      setBio(data.bio || '');
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Impossible de charger le profil');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileUpdating(true);
    setProfileSuccess('');
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/profile/me', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          full_name: fullName,
          bio,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update profile');
      }

      const data = await response.json();
      setProfile(data);
      localStorage.setItem('username', data.username);
      setProfileSuccess('Profil mis à jour avec succès');

      // Refresh the page to update header
      setTimeout(() => window.location.reload(), 1500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setProfileUpdating(false);
    }
  };

  const handleEmailUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailUpdating(true);
    setEmailSuccess('');
    setEmailError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/profile/email', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_email: newEmail,
          current_password: emailPassword,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update email');
      }

      setEmailSuccess('Email mis à jour avec succès');
      setNewEmail('');
      setEmailPassword('');
      fetchProfile();
    } catch (err: any) {
      setEmailError(err.message);
    } finally {
      setEmailUpdating(false);
    }
  };

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordUpdating(true);
    setPasswordSuccess('');
    setPasswordError('');

    if (newPassword !== confirmPassword) {
      setPasswordError('Les mots de passe ne correspondent pas');
      setPasswordUpdating(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/profile/password', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update password');
      }

      setPasswordSuccess('Mot de passe mis à jour avec succès');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordError(err.message);
    } finally {
      setPasswordUpdating(false);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAvatarUploading(true);
    setAvatarError('');

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/profile/avatar', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to upload avatar');
      }

      fetchProfile();
    } catch (err: any) {
      setAvatarError(err.message);
    } finally {
      setAvatarUploading(false);
    }
  };

  const handleDeleteAvatar = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/profile/avatar', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete avatar');
      }

      fetchProfile();
    } catch (err: any) {
      setAvatarError(err.message);
    }
  };

  const handleAccountDeletion = async (e: React.FormEvent) => {
    e.preventDefault();

    if (deleteConfirmation !== 'DELETE') {
      setDeleteError('Veuillez taper "DELETE" pour confirmer la suppression');
      return;
    }

    if (!confirm('Cette action est irréversible. Êtes-vous absolument sûr de vouloir supprimer votre compte ?')) {
      return;
    }

    setDeleting(true);
    setDeleteError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/profile/me', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          password: deletePassword,
          confirmation: deleteConfirmation,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete account');
      }

      // Clear local storage and redirect
      localStorage.clear();
      router.push('/');
    } catch (err: any) {
      setDeleteError(err.message);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
          <div className="text-xl">Chargement...</div>
        </div>
      </>
    );
  }

  if (error && !profile) {
    return (
      <>
        <Header />
        <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
          <div className="text-xl text-red-500">{error}</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gray-900 text-white pt-20 px-4">
        <div className="max-w-4xl mx-auto py-8">
          <h1 className="text-3xl font-bold mb-8">Mon Profil</h1>

          {/* Avatar Section */}
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <div className="flex items-center space-x-6">
              <div className="relative">
                {profile?.avatar_url ? (
                  <img
                    src={getAvatarUrl(profile.avatar_url)}
                    alt="Avatar"
                    className="w-24 h-24 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-3xl font-bold">
                    {profile?.username?.charAt(0).toUpperCase()}
                  </div>
                )}
                {avatarUploading && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
                    <div className="text-sm">Chargement...</div>
                  </div>
                )}
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold">{profile?.username}</h2>
                <p className="text-gray-400">{profile?.email}</p>
                <div className="mt-4 flex space-x-4">
                  <label className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded cursor-pointer transition">
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleAvatarUpload}
                      disabled={avatarUploading}
                    />
                    Changer la photo
                  </label>
                  {profile?.avatar_url && (
                    <button
                      onClick={handleDeleteAvatar}
                      className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition"
                    >
                      Supprimer la photo
                    </button>
                  )}
                </div>
                {avatarError && <p className="text-red-500 mt-2">{avatarError}</p>}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex space-x-4 mb-6 border-b border-gray-700">
            <button
              onClick={() => setActiveTab('profile')}
              className={`pb-2 px-4 ${activeTab === 'profile' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-400'}`}
            >
              Informations
            </button>
            <button
              onClick={() => setActiveTab('email')}
              className={`pb-2 px-4 ${activeTab === 'email' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-400'}`}
            >
              Email
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`pb-2 px-4 ${activeTab === 'password' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-400'}`}
            >
              Mot de passe
            </button>
            <button
              onClick={() => setActiveTab('delete')}
              className={`pb-2 px-4 ${activeTab === 'delete' ? 'border-b-2 border-red-500 text-red-500' : 'text-gray-400'}`}
            >
              Supprimer le compte
            </button>
          </div>

          {/* Profile Information Tab */}
          {activeTab === 'profile' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Informations du profil</h2>
              <form onSubmit={handleProfileUpdate}>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Nom d'utilisateur</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    minLength={3}
                    maxLength={50}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Nom complet</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    maxLength={255}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Biographie</label>
                  <textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    maxLength={500}
                  />
                  <p className="text-sm text-gray-400 mt-1">{bio.length}/500 caractères</p>
                </div>
                {profileSuccess && <p className="text-green-500 mb-4">{profileSuccess}</p>}
                {error && <p className="text-red-500 mb-4">{error}</p>}
                <button
                  type="submit"
                  disabled={profileUpdating}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded disabled:opacity-50 transition"
                >
                  {profileUpdating ? 'Mise à jour...' : 'Mettre à jour'}
                </button>
              </form>
            </div>
          )}

          {/* Email Tab */}
          {activeTab === 'email' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Changer l'email</h2>
              <p className="text-gray-400 mb-4">Email actuel: {profile?.email}</p>
              <form onSubmit={handleEmailUpdate}>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Nouvel email</label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Mot de passe actuel</label>
                  <input
                    type="password"
                    value={emailPassword}
                    onChange={(e) => setEmailPassword(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                {emailSuccess && <p className="text-green-500 mb-4">{emailSuccess}</p>}
                {emailError && <p className="text-red-500 mb-4">{emailError}</p>}
                <button
                  type="submit"
                  disabled={emailUpdating}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded disabled:opacity-50 transition"
                >
                  {emailUpdating ? 'Mise à jour...' : 'Changer l\'email'}
                </button>
              </form>
            </div>
          )}

          {/* Password Tab */}
          {activeTab === 'password' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Changer le mot de passe</h2>
              <form onSubmit={handlePasswordUpdate}>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Mot de passe actuel</label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Nouveau mot de passe</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    minLength={8}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Confirmer le nouveau mot de passe</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    minLength={8}
                  />
                </div>
                {passwordSuccess && <p className="text-green-500 mb-4">{passwordSuccess}</p>}
                {passwordError && <p className="text-red-500 mb-4">{passwordError}</p>}
                <button
                  type="submit"
                  disabled={passwordUpdating}
                  className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded disabled:opacity-50 transition"
                >
                  {passwordUpdating ? 'Mise à jour...' : 'Changer le mot de passe'}
                </button>
              </form>
            </div>
          )}

          {/* Delete Account Tab */}
          {activeTab === 'delete' && (
            <div className="bg-gray-800 rounded-lg p-6 border-2 border-red-600">
              <h2 className="text-xl font-bold mb-4 text-red-500">Zone dangereuse</h2>
              <p className="text-gray-300 mb-4">
                La suppression de votre compte est permanente et irréversible. Toutes vos données seront supprimées définitivement.
              </p>
              <form onSubmit={handleAccountDeletion}>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Mot de passe</label>
                  <input
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">
                    Tapez "DELETE" pour confirmer
                  </label>
                  <input
                    type="text"
                    value={deleteConfirmation}
                    onChange={(e) => setDeleteConfirmation(e.target.value)}
                    className="w-full px-4 py-2 bg-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-red-500"
                    required
                    placeholder="DELETE"
                  />
                </div>
                {deleteError && <p className="text-red-500 mb-4">{deleteError}</p>}
                <button
                  type="submit"
                  disabled={deleting || deleteConfirmation !== 'DELETE'}
                  className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded disabled:opacity-50 transition"
                >
                  {deleting ? 'Suppression...' : 'Supprimer définitivement mon compte'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
