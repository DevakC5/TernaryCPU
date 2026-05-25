"""TensorCore — ternary tensor/ matrix multiply engine.

Supports matrix multiplication, batched matmul, vector-matmul,
and fused linear+activation operations, all in the ternary domain.
"""

from trinary.ai.activations import ternary_step, trit_to_signed, signed_to_trit


class TensorCore:
    """Ternary tensor compute engine.

    All operations use signed arithmetic internally and quantize
    results back to ternary digits via ternary_step.
    """

    @staticmethod
    def _to_signed_2d(mat):
        return [[trit_to_signed(x) for x in row] for row in mat]

    @staticmethod
    def _to_signed_1d(vec):
        return [trit_to_signed(x) for x in vec]

    @staticmethod
    def _validate_matmul(a_rows, a_cols, b_rows, b_cols):
        if a_cols != b_rows:
            raise ValueError(
                f"Incompatible matmul: ({a_rows}x{a_cols}) x ({b_rows}x{b_cols})"
            )

    def matmul(self, a, b):
        """Multiply two ternary matrices (or matrix x vector).

        Args:
            a: List of lists of ternary digits (matrix, rows x cols).
            b: List of lists of ternary digits (matrix, cols x cols2)
               OR list of ternary digits (vector, length cols).

        Returns:
            List of lists (matrix) or list (vector) of ternary digits.

        Raises:
            ValueError: If dimensions are incompatible.
        """
        rows_a = len(a)
        cols_a = len(a[0]) if a else 0

        if isinstance(b[0], list):
            rows_b = len(b)
            cols_b = len(b[0]) if b else 0
            self._validate_matmul(rows_a, cols_a, rows_b, cols_b)

            a_s = self._to_signed_2d(a)
            b_s = self._to_signed_2d(b)

            result = []
            for r in range(rows_a):
                row = []
                for c in range(cols_b):
                    total = sum(a_s[r][k] * b_s[k][c] for k in range(cols_a))
                    row.append(ternary_step(total))
                result.append(row)
            return result
        else:
            rows_b = len(b)
            self._validate_matmul(rows_a, cols_a, rows_b, 1)

            a_s = self._to_signed_2d(a)
            b_s = self._to_signed_1d(b)

            result = []
            for r in range(rows_a):
                total = sum(a_s[r][k] * b_s[k] for k in range(cols_a))
                result.append(ternary_step(total))
            return result

    def batch_matmul(self, batch_a, batch_b):
        """Batched matrix multiplication.

        Args:
            batch_a: List of matrices A.
            batch_b: List of matrices B (same length).

        Returns:
            List of result matrices.

        Raises:
            ValueError: If batch sizes differ.
        """
        if len(batch_a) != len(batch_b):
            raise ValueError(
                f"Batch size mismatch: {len(batch_a)} vs {len(batch_b)}"
            )
        return [self.matmul(a, b) for a, b in zip(batch_a, batch_b)]

    def fused_linear(self, weights, inputs, bias=None, activation=ternary_step):
        """Compute activation(W @ x + b) — a fused linear layer.

        Args:
            weights: Matrix of ternary digits (output_dims x input_dims).
            inputs: List of ternary digits (input_dims).
            bias: Optional list of ternary digits (output_dims).
            activation: Activation function (default ternary_step).

        Returns:
            List of ternary digits (output_dims).
        """
        outputs = self.matmul(weights, inputs)
        if bias is not None:
            if len(bias) != len(outputs):
                raise ValueError(
                    f"Bias length {len(bias)} != outputs {len(outputs)}"
                )
            signed_out = [trit_to_signed(o) for o in outputs]
            signed_b = [trit_to_signed(b) for b in bias]
            combined = [s_out + s_b for s_out, s_b in zip(signed_out, signed_b)]
            return [activation(v) for v in combined]
        return [activation(trit_to_signed(o)) for o in outputs]

    def tensor_add(self, a, b):
        """Element-wise addition of two ternary matrices.

        Args:
            a: Matrix of ternary digits.
            b: Matrix of ternary digits.

        Returns:
            Matrix of ternary digits.
        """
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            raise ValueError("Shape mismatch")
        rows, cols = len(a), len(a[0])
        result = []
        for r in range(rows):
            row = []
            for c in range(cols):
                s = trit_to_signed(a[r][c]) + trit_to_signed(b[r][c])
                row.append(ternary_step(s))
            result.append(row)
        return result

    def tensor_mul(self, a, b):
        """Element-wise multiplication of two ternary matrices.

        Args:
            a: Matrix of ternary digits.
            b: Matrix of ternary digits.

        Returns:
            Matrix of ternary digits.
        """
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            raise ValueError("Shape mismatch")
        rows, cols = len(a), len(a[0])
        result = []
        for r in range(rows):
            row = []
            for c in range(cols):
                s = trit_to_signed(a[r][c]) * trit_to_signed(b[r][c])
                row.append(ternary_step(s))
            result.append(row)
        return result
