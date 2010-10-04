

P = covariance_distance_uniform.result.cov_readings;
Pinv = pinv(P);
T = firstorder_distance_uniform.result.T;
Tx = squeeze(T(1,:,:));
Ty = squeeze(T(2,:,:));
Ttheta = squeeze(T(3,:,:));

figure; imagesc(P)


figure; nr=1;nc=2;np=1;

subplot(nr,nc,np); np=np+1;
imagesc(Ttheta)
title('Ttheta')

subplot(nr,nc,np); np=np+1;
imagesc(Pinv * Ttheta)
title('Pinv * Ttheta')


figure; nr=1;nc=2;np=1;

subplot(nr,nc,np); np=np+1;
imagesc(Tx)
title('Tx')

subplot(nr,nc,np); np=np+1;
imagesc(Pinv * Tx)
title('Pinv * Tx')


figure; nr=1;nc=2;np=1;

subplot(nr,nc,np); np=np+1;
imagesc(Ty)
title('Ty')

subplot(nr,nc,np); np=np+1;
imagesc(Pinv * Ty)
title('Pinv * Ty')
