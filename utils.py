import numpy as np
from numpy.linalg import LinAlgError
from numpy.linalg import cholesky
import matplotlib.pyplot as plt

def randncor(n, N, C):
    try:
        A = cholesky(C)
    except LinAlgError:
        m = 0
        print('A is not positive definite')
    m = n
    u = np.random.randn(m, N)
    x = A.conj().transpose().dot(u)
    return x

def score(p,p_,scoring = 'mea'):
    if scoring == 'mea':
        err = np.average(np.abs(p-p_))
    if scoring == 'mse':
        err  = np.average((p-p_)**2)
    return err

def parzen_window(x,train,h,kernel = 'gauss_diag'):

    """Probablity density estimation with given kernel function.
    
    Parameters
    ----------
    x : array-like, shape = [n_samples] or [n_dimensions, n_samples]
        
        
    train : array-like, shape = [n_samples] or [n_dimensions, n_samples]
        Training data
    
    h : float
        Window bandwidth
    
    kernel: {'gauss_diag','gauss_cov','exp','rect','tri'}
        Kernel to use in computations:
        
        - 'gauss_diag'
        
        - 'gauss_cov'
        
        - 'exp'
        
        - 'rect'
        
        - 'tri'
        
    Returns
    -------
    p_ : array, 
    Probability density estimation.
    
    """

    if x.ndim ==1:
        n1 = 1
        mx = x.shape[0]
    else:
        n1,mx = x.shape

    if train.ndim ==1:
        n2 = 1
        N = train.shape[0]
    else:
        n2,N = train.shape


    if n1 != n2:
        raise ValueError("Number of dimensions in x and train does not correspond:"
                         " %d != %d" % (n1, n2))
    if kernel not in ('gauss_diag','gauss_cov','exp','rect','tri','custom'):
        raise ValueError('Kernel %s not understood' % kernel)

    n = n1
    C = np.ones([n,n])
    C_ = C.copy()

   
    if kernel == 'gauss_cov' and N>1:
        C = np.zeros([n,n])
        m_ = np.transpose(np.mean(np.transpose(train),axis = 0))
        for i in range(N):
            C = C + np.matrix(train[:,i] - m_).T*(train[:,i] - m_)
        C=C/(N-1)
        C_=C**(-1)
    
    fit = np.zeros([N,mx])
    for i in range(N):
        p_k = np.zeros([n,mx])
        mx_i = np.tile(train[:,i].reshape(-1,1),[1,mx])

        if kernel == 'gauss_diag':
            ro = np.sum(np.asarray(x-mx_i)**2,0)
            fit[i,:] = np.exp(-ro/(2*h**2))/((2*np.pi)**(n/2)*(h**n))

        elif kernel == 'gauss_cov':
            d = x-mx_i
            dot = np.dot(C_,d)
            ro=np.sum(np.multiply(dot,d),0)
            fit[i,:]=np.exp(-ro/(2*h**2))*((2*np.pi)**(-n/2)*(h**(-n))*(np.linalg.det(C)**(-0.5)))


        elif kernel == 'exp':
            ro=np.abs(x-mx_i)/h
            fit[i,:]=np.prod(np.exp(-ro),0)/(2*h**n)

        elif kernel == 'rect':
            ro=np.abs(x-mx_i)/h
            for k in range(n):
                ind= np.nonzero(ro[k,:]<1)[1]
                p_k[k,[ind]]=1/2
            fit[i,:]=np.prod(p_k,axis = 0)/h**n

        elif kernel == 'tri':
            ro=np.abs(x-mx_i)/h
            for k in range(n):
                if n == 1:
                    ind= np.nonzero(ro[k,:]<1)[1]
                else:
                    ind= np.nonzero(ro[k,:]<1)
                p_k[k,[ind]]= 1-ro[k,[ind]]
            fit[i,:]=np.prod(p_k,axis = 0)/h**n
        
        elif kernel == 'custom':
            ro = np.asarray((x-mx_i)/h)**2
            fit[i,:] = (1/(np.pi*h))*(1/(1+ro))
        if N>1:
            p_ = np.sum(fit,0)/N
        else:
            p_ = fit
    return p_



def plot_err(h_N,errors):
    plt.plot(h_N,errors,'m');
    plt.xlabel('Ширина окна, h');
    plt.ylabel('Cредняя абсолютная ошибка');
    plt.title('График зависимости ошибки оценивания от величины параметра оконной функции');

