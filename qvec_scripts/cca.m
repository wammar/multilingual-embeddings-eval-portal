function score = cca(X_file, Y_file, results_file)

% print input files
X_file, Y_file, results_file

X = dlmread(X_file);
Y = dlmread(Y_file);

X = normr(X);
Y = normr(Y);

[Wx,Wx,r] = canoncorr(X, Y);

score = mean(r);

fprintf('QVEC score: %f\n',score);
fileID = fopen(results_file, 'w');
fprintf(fileID,'%f',score);
exit
