import {
    Body,
    Button,
    Container,
    Head,
    Hr,
    Html,
    Img,
    Column,
    Preview,
    Section,
    Text,
  } from '@react-email/components';
  import * as React from 'react';
  
  export const StripeWelcomeEmail = () => (
    <Html>
      <Head />
      <Preview>You're now ready to see your pokemon battle log!</Preview>
      <Body style={main}>
        <Container style={container}>
          <Section style={box}>
            <Img
              src="https://storage.googleapis.com/turing-alcove-157907-sandbox/poke_battle_logger_logo.png"
              width="260"
              height="50"
              alt="Stripe"
            />
            <Hr style={hr} />
            <Text style={paragraph}>
              Dear ユーザ名
            </Text>
            <Text style={paragraph}>
              The battle data analysis by Poke Battle Logger has been completed!
            </Text>
            <Text style={paragraph}>
              <ul>
                <li><Text style={paragraph}>Target Video: ここに動画リンク</Text></li>
                <li><Text style={paragraph}>Number of Added Logs: ここに対戦ログ数</Text></li>
                <li><Text style={paragraph}>Number of Win: ここに勝利数</Text></li>
                <li><Text style={paragraph}>Number of Lose: ここに敗北数</Text></li>
              </ul>
            </Text>
            <Button
              pX={10}
              pY={10}
              style={button}
              href="https://poke-battle-logger.vercel.app"
            >
              Visit Your Battle Log
            </Button>
            <Hr style={hr} />
            <Text style={paragraph}>
              If you do not recall receiving this email, I kindly ask that you please delete it.
            </Text>
            <Hr style={hr} />
            <Text style={footer}>
              Poke Battle Logger, Japan, @fufufukakaka
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
  
  export default StripeWelcomeEmail;
  
  const main = {
    backgroundColor: '#f6f9fc',
    fontFamily:
      '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Ubuntu,sans-serif',
  };
  
  const container = {
    backgroundColor: '#ffffff',
    margin: '0 auto',
    padding: '20px 0 48px',
    marginBottom: '64px',
  };
  
  const box = {
    padding: '0 48px',
  };
  
  const hr = {
    borderColor: '#e6ebf1',
    margin: '20px 0',
  };
  
  const paragraph = {
    color: '#525f7f',
  
    fontSize: '16px',
    lineHeight: '24px',
    textAlign: 'left' as const,
  };
  
  const anchor = {
    color: '#556cd6',
  };
  
  const button = {
    backgroundColor: '#3182CE',
    borderRadius: '5px',
    color: '#fff',
    fontSize: '16px',
    fontWeight: 'bold',
    textDecoration: 'none',
    textAlign: 'center' as const,
    display: 'block',
    width: '100%',
  };
  
  const footer = {
    color: '#8898aa',
    fontSize: '12px',
    lineHeight: '16px',
  };
  