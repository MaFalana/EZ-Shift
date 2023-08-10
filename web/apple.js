
document.addEventListener('musickitloaded', function() {
    // MusicKit global is now defined
    MusicKit.configure({
      developerToken: 'eyJhbGciOiJFUzI1NiIsImtpZCI6Ikg1WVpRNVpLWjQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJYMzM5Mkg3RzQ0IiwiaWF0IjoxNjkwMDQzNDQzLCJleHAiOjE3MDU1ODEwNDN9.FJCW0avc05cOUDHPETSAyKCuOfTCGaMok_msw6nyUoH2m_Ljqr9ufyK2PoBNnWz4AEUOWODJLaSQRL5eUKXnTw',
      app: {
        name: 'EZ-Shift',
        build: '1'
      }
    });
  });

  const music = MusicKit.getInstance();
  await music.authorize();