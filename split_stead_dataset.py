import json
import numpy as np
import h5py
from obspy import UTCDateTime



def stead_attributes_to_json(attrs):   

    tconv = lambda x: None if x == 'None' else float(x)

    arrival_time = UTCDateTime(attrs['source_origin_time']) + attrs['p_arrival_sample']/100.0

    event_type = attrs['trace_category']
    if 'earthquake' in event_type:
        event_type = 'earthquake'   # 'earthquake_local' -> just 'earthquake'

    info_dict = {
        'event_type': event_type,
        'event_type_certainty': 'known',
        'origins': [
            {
                'resource_id': attrs['source_id'],
                'time': attrs['source_origin_time'],
                'time_errors': {'uncertainty': tconv(attrs['source_origin_uncertainty_sec'])},
                'longitude': tconv(attrs['source_longitude']),
                'latitude': tconv(attrs['source_longitude']),
                'depth': tconv(attrs['source_depth_km']),
                'depth_errors': {'uncertainty': tconv(attrs['source_depth_uncertainty_km'])},
            }
        ],
        'magnitudes': [
            {
                'mag': tconv(attrs['source_magnitude']),
                'magnitude_type': attrs['source_magnitude_type'],
            }
        ],
        # Arrival times in 'our' lingo
        'est_arrivaltime_arces': arrival_time.__str__(),
        'analyst_pick_time': arrival_time.__str__(),
        
        # Distance/direction to station
        'dist_to_arces': tconv(attrs['source_distance_km']),
        'baz_to_arces': tconv(attrs['back_azimuth_deg']),
    
        'trace_stats': {
            'starttime': attrs['trace_start_time'],
            'sampling_rate': 100.0,
            'station': attrs['network_code'] + '.' + attrs['receiver_code'],
            'channels': ['East-West', 'North-South', 'Vertical']
        }
    }
    
    return json.dumps(info_dict)






if __name__ == '__main__':

    testfile = '/nobackup/steffen/STEAD/chunk2.hdf5'

    with h5py.File(testfile, 'r') as hfile:

        i = 0
        group = hfile.get('data')
        for eventname in group.keys():

            data = group[eventname]
            metadata = stead_attributes_to_json(data.attrs)
            
            with h5py.File(eventname+'.h5', 'w') as fout:
                fout.create_dataset('traces', data=np.array(data).T, dtype=np.float32)
                string_dt = h5py.special_dtype(vlen=str)
                fout.create_dataset('event_info', data=np.array(metadata, dtype='object'), dtype=string_dt)

    
