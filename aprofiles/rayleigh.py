#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Rayleigh Profile


from matplotlib import pyplot as plt

class Rayleigh:
    """Class for computing a standard rayleigh profile (backscatter and extinction)

    Attributes:
        altitude (array): array of altitude to be used to compute rayleigh profile, in m
        T0 (float): Temperature at ground level, in K
        P0 (float): Pressure at ground level, in hPa
        wavelength (float): Wavelength of rayleigh profile to be computed

    """

    def __init__(self,altitude=None, T0=298, P0=1013, wavelength=None):
        self.altitude = altitude
        self.T0 = T0
        self.P0 = P0
        self.wavelength = wavelength
    
    def standard_atmosphere(self):

        #standart gradients & parameters
        dTdz_tropo=-6.5;
        dTdz_strato=1.4;
        dTdz_meso=-2.4;
        z_tpause=13;
        z_spause=55; 
        p_He=8;

        #convert pressure from hPa to Pa
        p_z0=p_z0*100;
        #convert altitude to km
        z = z/1000;

        #n_tpause=round(interp1(z(1:$-1),1:length(z)-1,z_tpause,'nearest','extrap'));
        #n_spause=round(interp1(z(1:$-1),1:length(z)-1,z_spause,'nearest','extrap'));
        #Tz(1:n_tpause,1)=T0+dTdz_tropo.*z(1:n_tpause);
        #Tz(n_tpause+1:n_spause,1)=T0+dTdz_tropo.*z(n_tpause+1)+dTdz_strato.*(z(n_tpause+1:n_spause)-z(n_tpause+1));
        #Tz(n_spause+1:length(z),1)=T0+dTdz_tropo.*z(n_tpause+1)+dTdz_strato.*(z(n_spause+1)-z(n_tpause+1))+dTdz_meso.*(z(n_spause+1:$)-z(n_spause+1));
        #Pz=p_z0.*exp(-z./p_He);
  
        #N_m=Pz./(8.314/6.023e23.*Tz);
        #section_m=5.45*(550./evstr(lambda))^4.09*1e-32;
        #bmol=N_m.*section_m;
        #amol=8.0*%pi*bmol/3.0;
        #amol = [0,1,2,3,4,5]

        rayleigh = {
            "amol": [0,1,2,3,4,5],
            "bmol": [0,2,4,5,6,8],
            "altitude": altitude,
            "wavelength": wavelength
        }
        return rayleigh

  def main():
    import reader
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    apro_reader = reader.ReadProfiles(path)
    l2_data = apro_reader.read()

    import matplotlib.plt as plt
    altitude = l2_data.altitude.data
    wavelength = l2_data.l0_wavelength.data

    T0=298;p_z0=1013;
    rayleigh = Rayleigh(altitude,T0,p_z0,wavelength);
    #trayleigh=exp(-2*cumsum(amol)*vresol);
    #pr2_mol=bmol.*trayleigh;
    print(rayleigh["amol"])

if __name__ == '__main__':
    main()