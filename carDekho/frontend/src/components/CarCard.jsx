const FUEL_BADGE = {
  Petrol: 'bg-blue-100 text-blue-700',
  Diesel: 'bg-amber-100 text-amber-700',
  CNG: 'bg-green-100 text-green-700',
  Electric: 'bg-teal-100 text-teal-700',
  LPG: 'bg-orange-100 text-orange-700',
};

function formatPrice(rupees) {
  if (!rupees) return 'N/A';
  const lakhs = rupees / 100_000;
  return `₹${lakhs % 1 === 0 ? lakhs.toFixed(0) : lakhs.toFixed(2)} L`;
}

function formatKm(km) {
  if (!km) return 'N/A';
  if (km >= 100_000) return `${(km / 100_000).toFixed(1)} lakh km`;
  return `${(km / 1000).toFixed(0)}k km`;
}

function Spec({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex flex-col">
      <span className="text-xs text-gray-400">{label}</span>
      <span className="text-sm font-medium text-gray-800">{value}</span>
    </div>
  );
}

export default function CarCard({ car }) {
  const displayName = car.car_name || `${car.brand} ${car.model}`;
  const fuelClass = FUEL_BADGE[car.fuel_type] || 'bg-gray-100 text-gray-600';
  const approxYear = car.vehicle_age != null ? 2024 - car.vehicle_age : null;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow duration-200 flex flex-col">
      {/* Top bar accent */}
      <div className="h-1 rounded-t-2xl bg-gradient-to-r from-blue-500 to-indigo-500" />

      <div className="p-5 flex flex-col gap-4 flex-1">
        {/* Name + Price */}
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-bold text-gray-900 text-base leading-snug truncate">
              {displayName}
            </h3>
            {approxYear && (
              <p className="text-gray-400 text-xs mt-0.5">{approxYear} model</p>
            )}
          </div>
          <span className="text-blue-600 font-bold text-base whitespace-nowrap">
            {formatPrice(car.selling_price)}
          </span>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-1.5">
          {car.fuel_type && (
            <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${fuelClass}`}>
              {car.fuel_type}
            </span>
          )}
          {car.transmission_type && (
            <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-700">
              {car.transmission_type}
            </span>
          )}
          {car.seller_type && (
            <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-600">
              {car.seller_type}
            </span>
          )}
        </div>

        {/* Specs grid */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-3 pt-1 border-t border-gray-50">
          <Spec label="KM Driven" value={formatKm(car.km_driven)} />
          <Spec label="Mileage" value={car.mileage ? `${car.mileage} kmpl` : null} />
          <Spec label="Engine" value={car.engine ? `${car.engine} cc` : null} />
          <Spec label="Power" value={car.max_power ? `${car.max_power} bhp` : null} />
          <Spec label="Seats" value={car.seats} />
          {car.vehicle_age != null && (
            <Spec label="Age" value={`${car.vehicle_age} yr${car.vehicle_age !== 1 ? 's' : ''} old`} />
          )}
        </div>
      </div>
    </div>
  );
}
