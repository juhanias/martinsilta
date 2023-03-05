import discord
import requests

from src.libs.folipy import cache


class Foli:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FöliPy/1.0.0 (python-requests/2.25.1)",
            "Accept": "application/json",
            "From": "juhani.astikainen@gmail.com",
        })
        self.cache = {}
        for category in self.get_categories():
            self.cache[category["category"]] = category["descr_fi"]

    def get_announcements(self):
        announcements = self.session.get("http://data.foli.fi/alerts").json()
        return announcements["global_message"], announcements["emergency_message"], announcements["messages"]

    def get_categories(self):
        return self.session.get("http://data.foli.fi/alerts/categories").json()


def potentially_null(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    else:
        return None


class Bussitutka:
    def __init__(self):
        self.url = 'http://data.foli.fi/'
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FöliPyBussiTutka/1.0.0 (python-requests/2.25.1; juhani.astikainen@gmail.com)",
            "Accept": "application/json",
            "From": "juhani.astikainen@gmail.com",
        })
        self.stops = {}

    def get_live_vehicles(self):
        live_vehicles = []
        all_vehicles = self.session.get(self.url + "/siri/vm").json()['result']['vehicles']
        for vehicle in all_vehicles:
            if all_vehicles[vehicle]['monitored']:
                live_vehicles.append(Vehicle(all_vehicles[vehicle]))
        cache.vehicles_cache = live_vehicles
        return live_vehicles

    def get_live_vehicles_by_line(self, line, from_cache=True):
        live_vehicles = []
        if from_cache:
            for vehicle in cache.vehicles_cache:
                if vehicle.line == line:
                    live_vehicles.append(vehicle)
            return live_vehicles
        else:
            all_vehicles = self.session.get(self.url + "/siri/vm").json()['result']['vehicles']
            for vehicle in all_vehicles:
                if all_vehicles[vehicle]['monitored'] and all_vehicles[vehicle]['lineref'] == line:
                    live_vehicles.append(Vehicle(all_vehicles[vehicle]))
            return live_vehicles

    def get_live_vehicles_coords_by_line(self, line):
        live_vehicles = self.get_live_vehicles_by_line(line)
        coords = []
        for vehicle in live_vehicles:
            coords.append(vehicle.get_location())
        return coords


class Vehicle:
    def __init__(self, vehicle_data):
        # https://data.foli.fi/siri/sm -> vehicles
        self.expected_arrival_time = potentially_null(vehicle_data, 'expectedarrivaltime')
        self.destionation_display = potentially_null(vehicle_data, 'destinationdisplay')

        # https://data.foli.fi/siri/vm -> vehicles
        self.vehicle_data = vehicle_data
        self.recorded_at_time = potentially_null(vehicle_data, 'recordedattime')
        self.valid_until_time = potentially_null(vehicle_data, 'validuntiltime')
        self.link_distance = potentially_null(vehicle_data, 'linkdistance')
        self.percentage = potentially_null(vehicle_data, 'percentage')
        self.line_ref = potentially_null(vehicle_data, 'lineref')
        self.direction_ref = potentially_null(vehicle_data, 'directionref')
        self.published_line_name = potentially_null(vehicle_data, 'publishedlinename')
        self.operator_ref = potentially_null(vehicle_data, 'operatorref')
        self.origin_ref = potentially_null(vehicle_data, 'originref')
        self.origin_name = potentially_null(vehicle_data, 'originname')
        self.destination_ref = potentially_null(vehicle_data, 'destinationref')
        self.destination_name = potentially_null(vehicle_data, 'destinationname')
        self.original_aimed_departure_time = potentially_null(vehicle_data, 'originalaimeddeparturetime')
        self.destination_aimed_arrival_time = potentially_null(vehicle_data, 'destinationaimedarrivaltime')
        self.monitored = potentially_null(vehicle_data, 'monitored')
        self.incongestion = potentially_null(vehicle_data, 'incongestion')
        self.in_panic = potentially_null(vehicle_data, 'inpanic')
        self.longitude = potentially_null(vehicle_data, 'longitude')
        self.latitude = potentially_null(vehicle_data, 'latitude')
        self.delay = potentially_null(vehicle_data, 'delay')
        self.delay_secs = potentially_null(vehicle_data, 'delaysecs')
        self.block_ref = potentially_null(vehicle_data, 'blockref')
        self.vehicle_ref = potentially_null(vehicle_data, 'vehicleref')
        self.next_stop_point_ref = potentially_null(vehicle_data, 'next_stoppointref')
        self.next_visit_number = potentially_null(vehicle_data, 'next_visitnumber')
        self.next_stop_point_name = potentially_null(vehicle_data, 'next_stoppointname')
        self.vehicle_at_stop = potentially_null(vehicle_data, 'vehicleatstop')
        self.next_destination_display = potentially_null(vehicle_data, 'next_destinationdisplay')
        self.next_aimed_arrival_time = potentially_null(vehicle_data, 'next_aimedarrivaltime')
        self.next_expected_arrival_time = potentially_null(vehicle_data, 'next_expectedarrivaltime')
        self.next_aimed_departure_time = potentially_null(vehicle_data, 'next_aimeddeparturetime')
        self.origin_name_sv = potentially_null(vehicle_data, 'originname_sv')
        self.destination_name_sv = potentially_null(vehicle_data, 'destinationname_sv')
        self.next_stop_point_name_sv = potentially_null(vehicle_data, 'next_stoppointname_sv')
        self.next_destination_display_sv = potentially_null(vehicle_data, 'next_destinationdisplay_sv')
        self.onward_calls = potentially_null(vehicle_data, 'onwardcalls')
        self.trip_ref = potentially_null(vehicle_data, '__tripref')
        self.route_ref = potentially_null(vehicle_data, '__routeref')
        self.direction_id = potentially_null(vehicle_data, '__directionid')

    def get_vehicle_data(self):
        return self.vehicle_data

    def get_location(self):
        return self.latitude, self.longitude

    def get_route(self):
        return Route(self.route_ref)

    def __str__(self):
        return f"Vehicle {self.vehicle_ref} on linjalla {self.line_ref} kohti {self.destination_name}."


class Route:
    def __init__(self, route_id):
        self.route_id = route_id
        self.url = 'http://data.foli.fi/'
        self.session = requests.Session()
        self.route_data = self.session.get(
            self.url + f"gtfs/v0/{cache.latest_gtfs_dataset}/trips/route/" + route_id).json()

    def get_route_shape(self):
        return Shape(self.route_data[0]['shape_id'])


class Shape:
    def __init__(self, shape_id):
        self.shape_id = shape_id
        self.url = 'http://data.foli.fi/'
        self.session = requests.Session()
        self.shape_data = self.session.get(self.url + f"gtfs/v0/{cache.latest_gtfs_dataset}/shapes/" + shape_id).json()


class Stop:
    def __init__(self, stop_data):
        self.stop_data = stop_data
        self.stop_code = potentially_null(stop_data, 'stop_code')
        self.stop_name = potentially_null(stop_data, 'stop_name')
        self.stop_desc = potentially_null(stop_data, 'stop_desc')
        self.stop_lat = potentially_null(stop_data, 'stop_lat')
        self.stop_lon = potentially_null(stop_data, 'stop_lon')
        self.zone_id = potentially_null(stop_data, 'zone_id')
        self.stop_url = potentially_null(stop_data, 'stop_url')
        self.location_type = potentially_null(stop_data, 'location_type')
        self.parent_station = potentially_null(stop_data, 'parent_station')
        self.stop_timezone = potentially_null(stop_data, 'stop_timezone')
        self.wheelchair_boarding = potentially_null(stop_data, 'wheelchair_boarding')

    def get_closest_vehicle(self, line):
        _data = requests.get("http://data.foli.fi/siri/sm/" + self.stop_code).json()
        _closest_vehicle = None
        _rest_of_vehicles = []
        _closest_vehicle_est_arrival = None
        for vehicle in _data['result']:
            if vehicle['lineref'] == line:
                vehicle = Vehicle(vehicle)
                if _closest_vehicle is None:
                    _closest_vehicle = vehicle
                    _closest_vehicle_est_arrival = vehicle.expected_arrival_time
                else:
                    if vehicle.expected_arrival_time < _closest_vehicle_est_arrival:
                        _closest_vehicle = vehicle
                        _closest_vehicle_est_arrival = vehicle.expected_arrival_time

                _rest_of_vehicles.append(vehicle)

        _rest_of_vehicles.pop(_rest_of_vehicles.index(_closest_vehicle))
        return _closest_vehicle, _rest_of_vehicles


class BussitutkaTask:
    def __init__(self, taskData):
        self.taskData = taskData
        self.taskAuthor = taskData['taskAuthor']
        self.taskChannel = taskData['taskChannel']
        self.taskMessage = taskData['taskMessage']
        self.taskStop = taskData['taskStop']
        self.taskLine = taskData['taskLine']

    async def update(self, bot: discord.Bot):
        linja = self.taskLine
        pysakki = self.taskStop
        stop = cache.stops_cache[pysakki]
        message = self.taskMessage

        closest_vehicle, closest_vehicles = stop.get_closest_vehicle(linja)

        response_embed_1 = discord.Embed(
            title=f"Bussitutka valvoo linjaa {linja} pysäkiltä {pysakki}"
        )

        response_embed_1.description = ""

        response_embed_1.description += f"**Lähin ajoneuvo**\n🚌 **{closest_vehicle.line_ref} - {closest_vehicle.vehicle_data['destinationdisplay']}** (<t:{closest_vehicle.vehicle_data['expecteddeparturetime']}:R>)\n\n**Muut ajoneuvot**\n"

        for vehicle in closest_vehicles:
            response_embed_1.description += f"🚌 **{vehicle.line_ref} - {vehicle.vehicle_data['destinationdisplay']}** (<t:{vehicle.vehicle_data['expecteddeparturetime']}:R>)\n"

        response_embed_2 = discord.Embed(
            title=f"Lähin bussi"
        )

        closest_vehicle_cache = None
        for vehicle in cache.vehicles_cache:
            if vehicle.vehicle_ref == closest_vehicle.vehicle_ref:
                closest_vehicle_cache = vehicle
                break

        print(closest_vehicle_cache.vehicle_data)
        response_embed_2.description = f"🚌 {closest_vehicle.line_ref} - {closest_vehicle.vehicle_data['destinationdisplay']}\n\n**Seuraava pysäkki: {closest_vehicle_cache.vehicle_data['next_stoppointname']}\n**Aikataulun mukainen saapumisaika: <t:{closest_vehicle.vehicle_data['aimeddeparturetime']}:R>**\n**Odotettu saapumisaika: <t:{closest_vehicle.vehicle_data['expecteddeparturetime']}:R>\n\n"
        response_embed_2.description += f"**Saapuu pysäkillesi (arvio): <t:{closest_vehicle.vehicle_data['expectedarrivaltime']}:t>**\n\n"
        try:
            message = await message.edit_original_response(embeds=[response_embed_1, response_embed_2])
        except discord.errors.NotFound:
            # Message was most likely deleted mid-refresh
            pass
