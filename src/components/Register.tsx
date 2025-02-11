import React from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

const Register: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data: any) => {
    try {
      const response = await axios.post('/api/register', data);
      console.log('Registration successful:', response.data);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="username">Username</label>
        <input id="username" {...register('username', { required: true })} />
        {errors.username && <span>This field is required</span>}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email', { required: true })} />
        {errors.email && <span>This field is required</span>}
      </div>
      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" {...register('password', { required: true, minLength: 6 })} />
        {errors.password && <span>Password must be at least 6 characters long</span>}
      </div>
      <button type="submit">Register</button>
    </form>
  );
};

export default Register;
