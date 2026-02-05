import React from "react";
import type { InterpolationResponseWithMetadata } from "../types";

interface ResultCardProps {
  data: InterpolationResponseWithMetadata;
}

const METHOD_NAMES: Record<string, string> = {
  lagrange: "Lagrange Interpolacija",
  newton_forward: "Newtonova Interpolacija Unaprijed",
  newton_backward: "Newtonova Interpolacija Unazad",
  direct: "Direktna Interpolacija",
};

const ResultCard: React.FC<ResultCardProps> = ({ data }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm my-4 max-w-3xl w-full">
      <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
        <span className="font-semibold text-gray-700 capitalize">
          {METHOD_NAMES[data.method] || data.method.replace(/_/g, " ")}
        </span>
        <span className="text-xs text-gray-500 font-mono">
          Stepen: {data.polynomial_degree}
        </span>
      </div>

      <div className="p-6 space-y-6">
        {/* Points Table */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2 uppercase tracking-wide">
            Ulazne tačke
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.points.map((p, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-red-50 text-red-700 font-mono"
              >
                ({p[0]}, {p[1]})
              </span>
            ))}
          </div>
        </div>

        {/* Polynomial Form */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2 uppercase tracking-wide">
            Polinomska jednačina
          </h4>
          <div className="bg-blue-50 p-3 rounded-lg font-mono text-sm text-blue-700 break-words">
            P(x) = {data.coefficients.map((c, i) => {
              // 1. Skip very small/zero coefficients to keep the equation clean
              if (Math.abs(c) < 0.00001) return null;

              const isNegative = c < 0;
              const absValue = Math.abs(c).toFixed(4);
              
              // 2. Determine the operator
              let sign = "";
              if (i === 0) {
                // First term: only show sign if negative
                sign = isNegative ? "-" : "";
              } else {
                // Subsequent terms: always show + or -
                sign = isNegative ? " - " : " + ";
              }

              return (
                <span key={i}>
                  {sign}{absValue}
                  {i > 0 && "x"}
                  {i > 1 && <sup>{i}</sup>}
                </span>
              );
            })}
          </div>
        </div>

        {/* Interpolated Results */}
        {data.formatted_results && data.formatted_results.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2 uppercase tracking-wide">
              Interpolirane vrijednosti
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.formatted_results.map((res, i) => (
                <span
                  key={i}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-green-50 text-green-700 font-mono"
                >
                   P({res[0]}) ≈ {res[1].toFixed(6)}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Graph */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2 uppercase tracking-wide">
            Vizualizacija
          </h4>
          <div className="border border-gray-100 rounded-lg overflow-hidden bg-white flex justify-center">
            <img
              src={`data:image/png;base64,${data.image_base64}`}
              alt="Graf interpolacije"
              className="max-w-full h-auto"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;
