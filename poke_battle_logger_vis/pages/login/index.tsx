import * as React from 'react';
import { useAuth0 } from "@auth0/auth0-react";
import { Button } from '@/components/ui/button';

export const Login = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <div className="h-screen flex flex-col justify-center">
      <div className="flex-grow flex items-center justify-center">
        <div className="flex flex-col items-center space-y-8">
          <h1 className="text-6xl font-bold">PokeBattleLogger</h1>
          <Button
            size="lg"
            onClick={() => loginWithRedirect()}
          >
            ログイン
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Login;
